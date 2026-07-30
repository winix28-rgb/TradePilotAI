"""Generic pipeline framework for the TradePilotAI OS."""

from .base import BasePipeline
from .context import PipelineContext
from .stage import PipelineStage

__all__ = ["BasePipeline", "PipelineContext", "PipelineStage"]
