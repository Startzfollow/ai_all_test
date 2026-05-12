# Accuracy Optimization Guide

This guide explains how to improve the project after product smoke acceptance has passed but accuracy is still weak.

## 1. RAG Accuracy

Common failure mode: the answer is wrong because the retriever did not recall the right chunk.

Recommended actions:

1. Build a 20-100 item QA evaluation set.
2. Tune `chunk_size` and `chunk_overlap`.
3. Preserve metadata: source, page, section, timestamp and document type.
4. Use a stronger embedding model for Chinese/multilingual data, such as `bge-m3` or `bge-large-zh-v1.5`.
5. Add hybrid retrieval: dense vectors + BM25 keyword retrieval.
6. Retrieve top-20 chunks, rerank, then send top-5 to the model.
7. Force answer citations and allow the model to say "not found in provided sources".

Evaluation indicators:

- Recall@3 / Recall@4
- source coverage
- citation correctness
- hallucination rate by manual review

## 2. YOLO Accuracy

Common failure mode: the model is fast but inaccurate on domain images.

Recommended actions:

1. Compare `yolov8n.pt` and `yolov8s.pt`.
2. Sweep `conf` and `iou` thresholds.
3. Build a small labeled validation set for the actual business scenario.
4. Fine-tune on domain data.
5. Report Precision, Recall, mAP50 and mAP50-95.
6. Only export ONNX/TensorRT after selecting an accuracy-qualified checkpoint.

Speed benchmark alone is not accuracy evidence.

## 3. LLaVA / Multimodal VQA Accuracy

Common failure mode: data format is valid, but the trained model does not answer correctly.

Recommended actions:

1. Build `data/eval/llava_vqa_100.jsonl` with manually verified image-question-answer triples.
2. Use a fixed inference prompt template.
3. Evaluate baseline model before LoRA fine-tuning.
4. Run 1k smoke training and verify loss decreases.
5. Compare base model vs LoRA adapter on the same evaluation set.
6. Record exact match, keyword match, ANLS or human review scores.

Do not claim completed large-scale training until logs, metrics and inference examples are recorded.

## 4. GUI Agent Accuracy

Common failure mode: the plan looks plausible but omits necessary steps or includes unsafe actions.

Recommended actions:

1. Create 20+ task cases with `required_steps` and `forbidden_actions`.
2. Keep dry-run mode as the default.
3. Add human confirmation for destructive operations.
4. Measure task success rate, step validity and unsafe action rate.
5. Save trace timelines for failed cases and use them to refine prompts and schemas.

GUI Agent quality should prioritize safety and traceability over autonomy.
