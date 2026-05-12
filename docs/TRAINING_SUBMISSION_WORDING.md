# Submission Wording for Training Capability

This document provides safe wording for resumes, registration forms, GitHub README sections, and project interviews.

## Recommended Project Description

> I built and organized a fullstack multimodal AI engineering project covering RAG knowledge-base QA, GUI Agent planning and trace recording, LLaVA-style multimodal data preparation and LoRA/QLoRA training, YOLO local inference acceleration, FastAPI backend services, and a React frontend dashboard. The project includes multi-GPU training scripts, DeepSpeed configuration, dataset validation, training evidence collection, evaluation outputs, and deployment-oriented APIs.

## Stronger Wording After Real Runs

Use this only after logs and metrics are available:

> I completed multi-GPU LLaVA-style LoRA fine-tuning experiments on local multimodal datasets, recorded training logs and metrics, and integrated the resulting inference workflow into the project backend.

## Avoid These Claims Unless You Have Direct Evidence

Do not claim:

- the model beats a public benchmark unless you ran that benchmark
- full official LLaVA reproduction unless all official stages were reproduced
- production deployment unless there is a reachable deployed service
- TensorRT speedup unless benchmark JSON and hardware details are available
- large-scale training completion unless logs, metrics, and checkpoints exist locally

## Interview Explanation Template

> The repository separates algorithm training and application engineering. For training, I prepared LLaVA-style data conversion, validation, LoRA/QLoRA configs, DeepSpeed launch scripts, and evidence collection. For application engineering, I connected RAG, GUI Agent planning, vision inference, and YOLO acceleration through FastAPI and a React demo dashboard. Large weights and datasets are excluded from Git, but the scripts and reports show how the experiments are reproduced locally.
