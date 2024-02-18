import dataclasses as dc
import os
import typing as t
from copy import deepcopy
from functools import wraps

import torch
import transformers
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)
from transformers.integrations.deepspeed import is_deepspeed_zero3_enabled

from superduperdb import logging
from superduperdb.base.artifact import Artifact
from superduperdb.base.build import build_datalayer
from superduperdb.base.config import Config

if t.TYPE_CHECKING:
    from datasets import Dataset

    from superduperdb.base.datalayer import Datalayer
    from superduperdb.ext.llm import LLM


class LLMCallback(TrainerCallback):
    def __init__(
        self,
        cfg: t.Optional["Config"] = None,
        identifier: t.Optional[str] = None,
        db: t.Optional["Datalayer"] = None,
        llm: t.Optional["LLM"] = None,
    ):
        self.cfg = cfg
        self.identifier = identifier
        self.db = db
        self.llm = llm

        # If we run training on remote, we need to provide identifier and cfg,
        # then can connect to db and load llm
        is_remote_init = self.identifier is not None and self.cfg is not None

        # If we run training on local, we can provide db and llm directly
        is_local_init = self.db is not None and self.llm is not None

        if not (is_remote_init or is_local_init):
            raise ValueError(
                "Please provide either (identifier and cfg) or (db and llm)"
            )

    def on_save(self, args, state, control, **kwargs):
        """Event called after a checkpoint save."""

        self.check_init()
        checkpoint_path = transformers.trainer.get_last_checkpoint(args.output_dir)
        if checkpoint_path is None:
            logging.warn("No checkpoint found, skip saving checkpoint")
            return

        self.llm.adapter_id = Artifact(checkpoint_path, serializer="zip")
        self.db.replace(self.llm, upsert=True)

    def check_init(self):
        # Rebuild datalayer for the new process
        if self.db is None:
            self.db = build_datalayer(self.cfg)
            self.llm = self.db.load("model", self.identifier)


@dc.dataclass
class LLMTrainingArguments(TrainingArguments):
    """
    LLM Training Arguments.
    Inherits from :class:`transformers.TrainingArguments`.

    {training_arguments_doc}
        use_lora (`bool`, *optional*, defaults to True):
            Whether to use LoRA training.
        lora_r (`int`, *optional*, defaults to 8):
            Lora R dimension.

        lora_alpha (`int`, *optional*, defaults to 16):
            Lora alpha.

        lora_dropout (`float`, *optional*, defaults to 0.05):
            Lora dropout.

        lora_target_modules (`List[str]`, *optional*, defaults to None):
            Lora target modules. If None, will be automatically inferred.

        lora_bias (`str`, *optional*, defaults to "none"):
            Lora bias.

        max_length (`int`, *optional*, defaults to 512):
            Maximum source sequence length during training.
        log_to_db (`bool`, *optional*, defaults to True):
            Log training to db.
            If True, will log checkpoint to superduperdb,
                but need ray cluster can access to db.
            If can't access to db, please set it to False.
    """

    __doc__ = __doc__.format(training_arguments_doc=TrainingArguments.__doc__)

    use_lora: bool = True
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: t.Optional[t.List[str]] = None
    lora_bias: t.Literal["none", "all", "lora_only"] = "none"
    bits: t.Optional[int] = None
    max_length: int = 512
    log_to_db: bool = False

    def __post_init__(self):
        ...
        # Overwrite __post_init__ for lazy build
        # Cause we can run on remote ray, that can avoid building error on client side

    def build(self):
        super().__post_init__()


def tokenize(tokenizer, example, X, y):
    """Function to tokenize the example."""
    prompt = example[X]

    prompt = prompt + tokenizer.eos_token
    result = tokenizer(
        prompt,
        truncation=True,
        max_length=tokenizer.model_max_length,
        padding="max_length",
    )
    result["labels"] = result["input_ids"].copy()
    return result


def train(
    training_config: dict,
    train_dataset: "Dataset",
    eval_datasets: t.Union["Dataset", t.Dict[str, "Dataset"]],
    model_kwargs: dict,
    tokenizer_kwargs: dict,
    X: t.Optional[str] = None,
    y: t.Optional[str] = None,
    db: t.Optional["Datalayer"] = None,
    llm: t.Optional["LLM"] = None,
    on_ray: t.Optional[bool] = False,
    ray_address: t.Optional[str] = None,
    ray_configs: t.Optional[dict] = None,
    **kwargs,
):
    """
    Train LLM model on specified dataset.
    The training process can be run on these following modes:
    - Local node without ray, but only support single GPU
    - Local node with ray, support multi-nodes and multi-GPUs
    - Remote node with ray, support multi-nodes and multi-GPUs

    If run locally, will use train_func to train the model.
        Can log the training process to db if db and llm provided.
        Will reuse the db and llm from the current process.
    If run on ray, will use ray_train to train the model.
        Can log the training process to db if db and llm provided.
        Will rebuild the db and llm for the new process that can access to db.
        The ray cluster must can access to db.

    Parameters:
    :param training_config: training config for LLMTrainingArguments
    :param train_dataset: training dataset
    :param eval_datasets: evaluation dataset, can be a dict of datasets
    :param model_kwargs: model kwargs for AutoModelForCausalLM
    :param tokenizer_kwargs: tokenizer kwargs for AutoTokenizer
    :param X: column name for input
    :param y: column name for output
    :param db: datalayer, used for creating LLMCallback
    :param llm: llm model, used for creating LLMCallback
    :param on_ray: whether to use ray, if True, will use ray_train
    :param ray_address: ray address, if not None, will run on ray cluster
    :param ray_configs: ray configs, must provide if using ray
    """

    training_args = LLMTrainingArguments(**training_config)
    if X:
        tokenizer = AutoTokenizer.from_pretrained(
            **tokenizer_kwargs,
        )
        tokenizer.model_max_length = training_config.get(
            "max_length", training_args.max_length
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        train_dataset = train_dataset.map(
            lambda example: tokenize(tokenizer, example, X, y),
            remove_columns=[
                X,
            ],
        )

        if isinstance(eval_datasets, dict):
            eval_datasets = {
                k: v.map(
                    lambda example: tokenize(tokenizer, example, X, y),
                    remove_columns=[
                        X,
                    ],
                )
                for k, v in eval_datasets.items()
            }
        else:
            eval_datasets = eval_datasets.map(
                lambda example: tokenize(tokenizer, example, X, y),
                remove_columns=[
                    X,
                ],
            )

    on_ray = on_ray or bool(ray_address) or bool(ray_configs)

    # Auto detect multi-GPUs and use ray to run data parallel training
    # If not todo this, will run on a bad parallel mode
    if not on_ray and torch.cuda.device_count() > 1:
        logging.warn("Detected multi-GPUs, will use ray to run training on multi-GPUs")
        on_ray = True
        from ray.train import ScalingConfig

        ray_configs = {
            "scaling_config": ScalingConfig(
                num_workers=torch.cuda.device_count(),
                use_gpu=True,
            )
        }
        logging.warn(f"Set ray_configs to {ray_configs}")
        logging.warn("Suggest to set ray_configs manually for better performance")

    log_to_db = training_args.log_to_db

    if not on_ray:
        # create local LLMCallback
        if db is not None and llm is not None and log_to_db:
            callbacks = [LLMCallback(db=db, llm=llm)]
        else:
            callbacks = None
        # build training_args for local training
        training_args.build()
        return train_func(
            training_args,
            train_dataset,
            eval_datasets,
            model_kwargs,
            tokenizer_kwargs,
            callbacks=callbacks,
            **kwargs,
        )

    else:
        # create remote LLMCallback, ray cluster must can access to db
        if db is not None and llm is not None and log_to_db:
            from superduperdb import CFG

            callbacks = [LLMCallback(cfg=CFG, identifier=llm.identifier)]
        else:
            callbacks = None
        results = ray_train(
            training_args,
            train_dataset,
            eval_datasets,
            model_kwargs=model_kwargs,
            tokenizer_kwargs=tokenizer_kwargs,
            callbacks=callbacks,
            ray_address=ray_address,
            ray_configs=ray_configs,
            **kwargs,
        )
        logging.info(f"Training finished, results: {results}")

        handle_ray_results(db, llm, results)
        return results


def handle_ray_results(db, llm, results):
    """
    Handle the ray results.
    Will save the checkpoint to db if db and llm provided.
    """
    checkpoint = results.checkpoint
    if checkpoint is None:
        logging.warn("No checkpoint found, skip saving checkpoint")
        return results
    path = checkpoint.path
    if checkpoint.filesystem.type_name == "s3":
        # download the checkpoint from s3
        logging.info(f"Download checkpoint from s3, {checkpoint}")
        path = checkpoint.to_directory()
        logging.info(f"Downloaded checkpoint to {path}")

    # Pad the path to the checkpoint
    path = os.path.join(path, "checkpoint")
    if llm is not None:
        llm.adapter_id = Artifact(path, serializer="zip")
        if db is not None:
            db.replace(llm, upsert=True)


def train_func(
    training_args: LLMTrainingArguments,
    train_dataset: "Dataset",
    eval_datasets: t.Union["Dataset", t.Dict[str, "Dataset"]],
    model_kwargs: dict,
    tokenizer_kwargs: dict,
    trainer_prepare_func: t.Optional[t.Callable] = None,
    callbacks=None,
    **kwargs,
):
    """
    Base training function for LLM model.
    :param training_args: training Arguments, see LLMTrainingArguments
    :param train_dataset: training dataset,
        can be huggingface datasets.Dataset or ray.data.Dataset
    :param eval_datasets: evaluation dataset, can be a dict of datasets
    :param model_kwargs: model kwargs for AutoModelForCausalLM
    :param tokenizer_kwargs: tokenizer kwargs for AutoTokenizer
    :param trainer_prepare_func: function to prepare trainer
        This function will be called after the trainer is created,
        we can add some custom settings to the trainer
    :param callbacks: list of callbacks will be added to the trainer
    :param **kwargs: other kwargs for Trainer
        All the kwargs will be passed to Trainer,
        make sure the Trainer support these kwargs
    """
    logging.info("Start training LLM model")
    logging.info(f"training_args: {training_args}")
    model_kwargs = deepcopy(model_kwargs)
    tokenizer_kwargs = deepcopy(tokenizer_kwargs)
    # Get device map
    device_map: t.Union[None, str, t.Dict[str, int]] = model_kwargs.get("device_map")
    if os.environ.get("LOCAL_RANK") is not None:
        ddp = int(os.environ.get("WORLD_SIZE", 1)) != 1
        device_map = {"": int(os.environ.get("LOCAL_RANK", "0"))} if ddp else None
    elif torch.backends.mps.is_available():
        device_map = "mps"

    quantization_config = create_quantization_config(training_args)

    if is_deepspeed_zero3_enabled():
        device_map = None
        model_kwargs["low_cpu_mem_usage"] = False
        if quantization_config is not None:
            raise ValueError(
                "Quantization is not supported with ZeRO-3. Please use ZeRO-2 instead."
            )

    logging.info("Overwriting model_kwargs for LLM training")
    logging.info(f"quantization_config: {quantization_config}")
    logging.info(f"device_map: {device_map}")

    model_kwargs["quantization_config"] = quantization_config
    model_kwargs["device_map"] = device_map
    logging.info(f"model_kwargs: {model_kwargs}")
    model = AutoModelForCausalLM.from_pretrained(
        **model_kwargs,
    )
    logging.info("tokenizer_kwargs: %s", tokenizer_kwargs)
    tokenizer = AutoTokenizer.from_pretrained(
        **tokenizer_kwargs,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.model_max_length = training_args.max_length or tokenizer.model_max_length

    if training_args.use_lora:
        logging.info("Preparing LoRA training")
        model = prepare_lora_training(model, training_args)

    trainer = Trainer(
        model=model,
        tokenizer=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_datasets,
        **kwargs,
    )
    if trainer_prepare_func is not None:
        trainer = trainer_prepare_func(trainer)

    for callback in callbacks or []:
        logging.info(f"Add callback {callback}")
        trainer.add_callback(callback)
    trainer.model.config.use_cache = False
    results = trainer.train()
    trainer.save_state()
    return results


@wraps(train_func)
def ray_train(
    training_args: LLMTrainingArguments,
    train_dataset,
    eval_datasets,
    ray_address: t.Optional[str] = None,
    ray_configs: t.Optional[t.Dict[str, t.Any]] = None,
    **kwargs,
):
    """
    Ray training function for LLM model.
    The ray train function will handle the following logic:
    - Prepare the datasets for ray
    - Build the training_loop_func for ray
    - Connect to ray cluster
    - Make some modifications to be compatible with ray finetune llm

    :param training_args: training Arguments, see LLMTrainingArguments
    :param train_dataset: training dataset,
        can be huggingface datasets.Dataset
    :param eval_datasets: evaluation dataset,
        Must be a Huggingface datasets.Dataset
    :param ray_address: ray address, if not None, will run on ray cluster
    :param ray_configs: ray configs, must provide if using ray_configs
    :param **kwargs: other kwargs for Trainer
    """
    import ray
    from ray import train
    from ray.train import ScalingConfig
    from ray.train.huggingface.transformers import (
        RayTrainReportCallback,
        prepare_trainer,
    )
    from ray.train.torch import TorchTrainer

    ray.data.DataContext.get_current().execution_options.verbose_progress = True

    def trainer_prepare_func(trainer):
        # TODO: Check issues of RayTrainReportCallback run on multi-nodes
        trainer.add_callback(RayTrainReportCallback())
        trainer = prepare_trainer(trainer)
        return trainer

    def ray_train_func(train_loop_config):
        os.environ["OMP_NUM_THREADS"] = str(
            train.get_context().get_trial_resources().bundles[-1].get("CPU", 1)
        )
        ray_train_ds = train.get_dataset_shard("train")
        ray_eval_ds = train.get_dataset_shard("eval")

        # TODO: Rebuild the datasets.Dataset to train_func
        # So that we can improve compatibility with llm training framework
        # For example: Dataset.from_generator(ray_train_ds.iter_rows)
        train_batch_size = train_loop_config["per_device_train_batch_size"]
        eval_batch_size = train_loop_config["per_device_eval_batch_size"]
        train_ds_iterable = ray_train_ds.iter_torch_batches(batch_size=train_batch_size)
        eval_ds_iterable = ray_eval_ds.iter_torch_batches(batch_size=eval_batch_size)

        kwargs["trainer_prepare_func"] = trainer_prepare_func

        # Note: Set use_reentrant to False when using ray+lora+gradient_checkpointing
        # If not, will cause error "Varibable has been marked as ready twice"
        # Seems to be some parameter compatibility issue between ray and peft
        if train_loop_config.get(
            "gradient_checkpointing", False
        ) and train_loop_config.get("use_lora", False):
            logging.warn(
                "Using Ray + LoRA + Gradient Checkpointing, set use_reentrant to False"
            )
            gradient_checkpointing_kwargs = (
                train_loop_config.get("gradient_checkpointing_kwargs", {}) or {}
            )
            gradient_checkpointing_kwargs["use_reentrant"] = False
            train_loop_config[
                "gradient_checkpointing_kwargs"
            ] = gradient_checkpointing_kwargs
        train_loop_args = LLMTrainingArguments(**train_loop_config)
        # Build the training_args on remote machine
        train_loop_args.build()
        return train_func(
            train_loop_args, train_ds_iterable, eval_ds_iterable, **kwargs
        )

    if ray_address is not None:
        ray.init(address=ray_address, ignore_reinit_error=True)

    ray_datasets = {
        "train": ray.data.from_huggingface(train_dataset),
        "eval": ray.data.from_huggingface(eval_datasets),
    }

    ray_configs = ray_configs or {}
    if "scaling_config" not in ray_configs:
        raise ValueError("Please provide scaling_config")

    if "run_config" not in ray_configs:
        logging.warn("No run_config provided")

    # Auto detect the max_steps from training_config if not provided
    # Can't use num_train_epochs, because it's not compatible with ray
    scaling_config: ScalingConfig = ray_configs["scaling_config"]
    if training_args.max_steps == -1 and isinstance(scaling_config.num_workers, int):
        logging.info("Auto detect max_steps from training_config")

        num_workers = scaling_config.num_workers
        per_device_train_batch_size = training_args.per_device_train_batch_size
        gradient_accumulation_steps = training_args.gradient_accumulation_steps

        step_size = (
            num_workers * per_device_train_batch_size * gradient_accumulation_steps
        )
        dataset_size = len(train_dataset)
        num_train_epochs = training_args.num_train_epochs
        max_steps = int(num_train_epochs * dataset_size / step_size)

        training_args.max_steps = max_steps
        logging.info(f"num_workers: {num_workers}")

        logging.info(f"Set max_steps to {max_steps}")

    trainer = TorchTrainer(
        train_loop_per_worker=ray_train_func,
        train_loop_config=training_args.to_dict(),
        datasets=ray_datasets,
        **ray_configs,
    )

    results = trainer.fit()
    return results


def prepare_lora_training(model, config: LLMTrainingArguments):
    """
    Prepare LoRA training for the model.
    Get the LoRA target modules and convert the model to peft model.
    """
    try:
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    except Exception as e:
        raise ImportError("Please install peft to use LoRA training") from e

    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        target_modules=config.lora_target_modules
        or get_lora_target_modules(model, config.bits),
        lora_dropout=config.lora_dropout,
        bias=config.lora_bias,
        task_type="CAUSAL_LM",
    )

    if config.bits:
        model = prepare_model_for_kbit_training(
            model,
            use_gradient_checkpointing=config.gradient_checkpointing,
        )

        ddp = int(os.environ.get("WORLD_SIZE", 1)) != 1
        if not ddp and torch.cuda.device_count() > 1:
            model.is_parallelizable = True
            model.model_parallel = True

    model = get_peft_model(model, lora_config)

    if config.gradient_checkpointing:
        model.enable_input_require_grads()

    if config.local_rank == 0:
        model.print_trainable_parameters()
    return model


def get_lora_target_modules(model, bits):
    """Find the LoRA target modules in the model."""
    try:
        import bitsandbytes as bnb
    except Exception as e:
        raise ImportError("Please install bitsandbytes to use LoRA training") from e

    if bits == 4:
        cls = bnb.nn.Linear4bit
    elif bits == 8:
        cls = bnb.nn.Linear8bitLt
    else:
        cls = torch.nn.Linear

    lora_module_names = set()
    for name, module in model.named_modules():
        if isinstance(module, cls):
            names = name.split(".")
            lora_module_names.add(names[0] if len(names) == 1 else names[-1])

    lora_module_names.discard("lm_head")
    return list(lora_module_names)


def create_quantization_config(config: LLMTrainingArguments):
    """Create quantization config for LLM training."""
    compute_dtype = (
        torch.float16
        if config.fp16
        else (torch.bfloat16 if config.bf16 else torch.float32)
    )
    if config.bits is not None:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=config.bits == 4,
            load_in_8bit=config.bits == 8,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )
    else:
        quantization_config = None
    return quantization_config
