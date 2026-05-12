import React, { useEffect, useState } from "react";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://localhost:8000";

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

export default function TaskCenterV4() {
  const [tasks, setTasks] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);

  async function refresh() {
    try {
      setStatus("loading");
      const data = await api("/api/business/v4/tasks");
      setTasks(data.items || []);
      setStatus("ready");
    } catch (err) {
      setError(String(err));
      setStatus("error");
    }
  }

  async function createTask(taskType) {
    await api("/api/business/v4/tasks", {
      method: "POST",
      body: JSON.stringify({ task_type: taskType, project_id: "default", payload: {} }),
    });
    await refresh();
  }

  async function runTask(taskId) {
    await api(`/api/business/v4/tasks/${taskId}/run`, { method: "POST" });
    await refresh();
  }

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="p-6 space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Task Center V4</h1>
        <p className="text-sm text-gray-600">Production-pilot task lifecycle dashboard.</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {["rag_build", "yolo_benchmark", "llava_train", "report_generate"].map((type) => (
          <button key={type} className="rounded-xl border px-3 py-2 shadow-sm" onClick={() => createTask(type)}>
            Create {type}
          </button>
        ))}
        <button className="rounded-xl border px-3 py-2 shadow-sm" onClick={refresh}>Refresh</button>
      </div>

      {status === "error" && <pre className="text-red-600">{error}</pre>}

      <div className="overflow-x-auto rounded-2xl border shadow-sm">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="bg-gray-50 text-left">
              <th className="p-3">Task</th>
              <th className="p-3">Type</th>
              <th className="p-3">Status</th>
              <th className="p-3">Progress</th>
              <th className="p-3">Result</th>
              <th className="p-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => (
              <tr key={task.task_id} className="border-t">
                <td className="p-3 font-mono text-xs">{task.task_id}</td>
                <td className="p-3">{task.task_type}</td>
                <td className="p-3">{task.status}</td>
                <td className="p-3">{Math.round((task.progress || 0) * 100)}%</td>
                <td className="p-3 font-mono text-xs">{task.result_uri || "-"}</td>
                <td className="p-3">
                  {task.status === "pending" && (
                    <button className="rounded-lg border px-2 py-1" onClick={() => runTask(task.task_id)}>Run</button>
                  )}
                </td>
              </tr>
            ))}
            {tasks.length === 0 && (
              <tr><td className="p-3" colSpan="6">No tasks yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
