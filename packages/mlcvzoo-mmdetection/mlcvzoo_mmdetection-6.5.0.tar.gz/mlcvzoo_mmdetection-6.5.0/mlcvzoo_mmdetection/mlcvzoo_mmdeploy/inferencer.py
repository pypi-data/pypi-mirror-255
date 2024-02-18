# Copyright Open Logistics Foundation
#
# Licensed under the Open Logistics Foundation License 1.3.
# For details on the licensing terms, see the LICENSE file.
# SPDX-License-Identifier: OLFL-1.3

"""Wrapper to run converted MMDetection models."""

from typing import List

import torch
from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape
from mmdet.apis.det_inferencer import InputsType
from mmdet.structures.det_data_sample import DetDataSample
from mmengine.config import Config

from mlcvzoo_mmdetection.configuration import MMDetectionMMDeployConfig
from mlcvzoo_mmdetection.utils import init_mm_config


class MMDeployInferencer:  # pylint: disable=too-few-public-methods
    """Inferencer for MMDetection models deployed with MMDeploy."""

    def __init__(
        self,
        model_config: Config,
        mmdeploy_config: MMDetectionMMDeployConfig,
    ) -> None:
        mmdeploy_cfg: Config = init_mm_config(mm_config=mmdeploy_config)

        self.task_processor = build_task_processor(
            model_cfg=model_config,
            deploy_cfg=mmdeploy_cfg,
            device=mmdeploy_config.device_string,
        )

        self.mmdeploy_model = self.task_processor.build_backend_model(
            model_files=mmdeploy_config.checkpoint_paths,
            data_preprocessor_updater=self.task_processor.update_data_preprocessor,
        )

        self._input_shape = get_input_shape(deploy_cfg=mmdeploy_cfg)

    def __call__(self, inputs: InputsType) -> List[DetDataSample]:
        """Run inference for given inputs.

        To be compatible with MMDetections DetInferencer, the __call__ method is used.

        Args:
            inputs (InputsType): The inputs to run an inference on.

        Returns:
            List[DetDataSample]: List of predictions.
        """
        model_inputs, _ = self.task_processor.create_input(
            imgs=inputs, input_shape=self._input_shape
        )

        with torch.no_grad():
            result: List[DetDataSample] = self.mmdeploy_model.test_step(model_inputs)

        return result
