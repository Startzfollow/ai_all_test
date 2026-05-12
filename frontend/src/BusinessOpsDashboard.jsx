import React, { useEffect, useState } from "react";
import { businessGet, businessPost } from "./businessOpsApi";

export default function BusinessOpsDashboard() {
  const [status, setStatus] = useState(null);
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [message, setMessage] = useState("");

  async function refresh() {
    setStatus(await businessGet("/status"));
    setProjects(await businessGet("/projects"));
    setTasks(await businessGet("/tasks"));
  }

  async function seedDemoTask(taskType) {
    const project = projects[0] || (await businessPost("/projects", { name: "Default Field Service Workspace" }));
    const params =
      taskType === "yolo_benchmark"
        ? { model: "weights/yolov8n.pt", image: "examples/images/demo.png", runs: 10 }
        : taskType === "llava_train"
          ? { allow_long_run: false }
          : taskType === "rag_build"
            ? { documents_dir: "examples/docs", top_k: 4 }
            : {};
    const task = await businessPost("/tasks", {
      project_id: project.id,
      task_type: taskType,
      title: `Run ${taskType}`,
      params,
    });
    const result = await businessPost(`/tasks/${task.id}/run`);
    setMessage(`${taskType}: ${result.status}`);
    await refresh();
  }

  useEffect(() => {
    refresh().catch((err) => setMessage(err.message));
  }, []);

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">设备巡检与售后知识助手</h1>
        <p className="text-gray-600">默认单工作台 UI：RAG 建库、YOLO benchmark、LLaVA 训练计划、报告生成、GPU 监控。</p>
      </div>

      {status && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="rounded-xl shadow p-4 bg-white"><b>Release</b><p>{status.release_stage}</p></div>
          <div className="rounded-xl shadow p-4 bg-white"><b>Database</b><p>{status.database_url_masked}</p></div>
          <div className="rounded-xl shadow p-4 bg-white"><b>GPU</b><p>{status.gpu_available ? "available" : "not detected"}</p></div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        {["rag_build", "yolo_benchmark", "llava_train", "report_generate"].map((t) => (
          <button key={t} onClick={() => seedDemoTask(t)} className="px-4 py-2 rounded-xl shadow bg-black text-white">
            Run {t}
          </button>
        ))}
      </div>

      {message && <div className="rounded-xl p-3 bg-gray-100">{message}</div>}

      <div className="rounded-xl shadow bg-white p-4">
        <h2 className="font-semibold mb-2">Tasks</h2>
        <table className="w-full text-sm">
          <thead><tr><th className="text-left">Type</th><th className="text-left">Title</th><th className="text-left">Status</th></tr></thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.id}><td>{task.task_type}</td><td>{task.title}</td><td>{task.status}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
