import React, { useEffect, useState } from 'react'
import { getJson, postJson } from './api.js'

const TABS = [
  ['dashboard', 'Dashboard'],
  ['rag', 'RAG Knowledge Base'],
  ['agent', 'GUI Agent Planner'],
  ['vlm', 'Multimodal VQA'],
  ['yolo', 'YOLO Inference'],
  ['system', 'System Monitor'],
]

function Panel({ title, children, eyebrow }) {
  return (
    <section className="panel">
      {eyebrow && <p className="eyebrow small">{eyebrow}</p>}
      <h2>{title}</h2>
      {children}
    </section>
  )
}

function JsonBlock({ data }) {
  return <pre className="json">{data ? JSON.stringify(data, null, 2) : '暂无结果'}</pre>
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function TraceTimeline({ trace }) {
  if (!trace?.length) return <p className="muted">暂无 trace。生成 GUI Agent 计划后会显示 observe → plan → safety → output。</p>
  return (
    <ol className="timeline">
      {trace.map((item, index) => (
        <li key={`${item.stage}-${index}`}>
          <strong>{item.stage}</strong>
          <span>{item.message}</span>
          <small>{item.timestamp_ms} ms</small>
        </li>
      ))}
    </ol>
  )
}

export default function App() {
  const [tab, setTab] = useState('dashboard')
  const [health, setHealth] = useState(null)
  const [status, setStatus] = useState(null)
  const [ragQuestion, setRagQuestion] = useState('这个项目覆盖了哪些 AI 技术栈？')
  const [ragResult, setRagResult] = useState(null)
  const [agentTask, setAgentTask] = useState('打开浏览器搜索 LLaVA 多模态微调流程')
  const [agentResult, setAgentResult] = useState(null)
  const [imagePath, setImagePath] = useState('examples/images/demo.png')
  const [vlmPrompt, setVlmPrompt] = useState('请描述图片内容')
  const [vlmResult, setVlmResult] = useState(null)
  const [yoloImage, setYoloImage] = useState('examples/images/demo.png')
  const [yoloModel, setYoloModel] = useState('weights/yolov8n.pt')
  const [yoloResult, setYoloResult] = useState(null)

  useEffect(() => {
    getJson('/api/system/health').then(setHealth).catch(err => setHealth({ ok: false, error: String(err) }))
    getJson('/api/system/status').then(setStatus).catch(err => setStatus({ ok: false, error: String(err) }))
  }, [])

  async function ingestDocs() {
    const result = await postJson('/api/rag/ingest', { documents_dir: 'examples/docs' })
    setRagResult(result)
  }

  async function askRag() {
    const result = await postJson('/api/rag/query', { question: ragQuestion, top_k: 4 })
    setRagResult(result)
  }

  return (
    <main className="container">
      <header className="hero">
        <p className="eyebrow">AI Fullstack Challenge Demo</p>
        <h1>Multimodal RAG Agent Suite</h1>
        <p className="subtitle">RAG、GUI Agent、LLaVA-style 微调入口、YOLO 加速与全栈展示的一体化工程实践。</p>
        <div className="hero-row">
          <div className="status">Backend: {health?.ok ? 'OK' : '未连接'}</div>
          <div className="status">RAG: {status?.rag_store || 'unknown'}</div>
          <div className="status">YOLO: {status?.yolo || 'unknown'}</div>
        </div>
      </header>

      <nav className="tabs">
        {TABS.map(([key, label]) => (
          <button key={key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </nav>

      {tab === 'dashboard' && (
        <div className="grid three">
          <Metric label="Backend" value={health?.ok ? 'Online' : 'Offline'} />
          <Metric label="Vector Store" value={status?.rag_store || 'local'} />
          <Metric label="YOLO Weights" value={status?.yolo || 'unknown'} />
          <Panel title="Module Status" eyebrow="overview">
            <ul className="checklist">
              <li>RAG: local JSON store demo + Qdrant adapter</li>
              <li>GUI Agent: dry-run action planning + trace timeline</li>
              <li>LLaVA/VLM: multimodal API and LoRA/QLoRA training entrypoint</li>
              <li>YOLO: local inference, ONNX/TensorRT export and benchmark script</li>
            </ul>
          </Panel>
          <Panel title="How to Demo" eyebrow="script">
            <pre className="json">python scripts/run_mini_demo.py{`\n`}bash scripts/run_backend.sh{`\n`}cd frontend && npm run dev</pre>
          </Panel>
        </div>
      )}

      {tab === 'rag' && (
        <Panel title="RAG 知识库问答" eyebrow="retrieval augmented generation">
          <div className="actions"><button onClick={ingestDocs}>导入 examples/docs</button></div>
          <textarea value={ragQuestion} onChange={e => setRagQuestion(e.target.value)} />
          <button onClick={askRag}>检索问答</button>
          <JsonBlock data={ragResult} />
        </Panel>
      )}

      {tab === 'agent' && (
        <div className="grid">
          <Panel title="GUI Agent 规划" eyebrow="dry-run only">
            <textarea value={agentTask} onChange={e => setAgentTask(e.target.value)} />
            <button onClick={() => postJson('/api/agent/gui/plan', { task: agentTask, dry_run: true }).then(setAgentResult)}>生成动作计划</button>
            <JsonBlock data={agentResult?.plan} />
          </Panel>
          <Panel title="Trace Timeline" eyebrow="observe / plan / safety / output">
            <TraceTimeline trace={agentResult?.trace} />
          </Panel>
        </div>
      )}

      {tab === 'vlm' && (
        <Panel title="LLaVA / VLM 图像问答" eyebrow="local endpoint or fallback">
          <label>Image path</label>
          <input value={imagePath} onChange={e => setImagePath(e.target.value)} />
          <label>Prompt</label>
          <textarea value={vlmPrompt} onChange={e => setVlmPrompt(e.target.value)} />
          <button onClick={() => postJson('/api/multimodal/llava/chat', { image_path: imagePath, prompt: vlmPrompt }).then(setVlmResult)}>多模态问答</button>
          <JsonBlock data={vlmResult} />
        </Panel>
      )}

      {tab === 'yolo' && (
        <Panel title="YOLO 本地推理" eyebrow="inference and acceleration workflow">
          <label>Image path</label>
          <input value={yoloImage} onChange={e => setYoloImage(e.target.value)} />
          <label>Model path</label>
          <input value={yoloModel} onChange={e => setYoloModel(e.target.value)} />
          <button onClick={() => postJson('/api/vision/yolo/infer', { image_path: yoloImage, model_path: yoloModel }).then(setYoloResult)}>检测</button>
          <JsonBlock data={yoloResult} />
        </Panel>
      )}

      {tab === 'system' && (
        <Panel title="System Monitor" eyebrow="runtime configuration">
          <JsonBlock data={status} />
        </Panel>
      )}
    </main>
  )
}
