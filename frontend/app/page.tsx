"use client";

import { useState } from "react";
import { createStoryboard, regenerateScene, Scene, Storyboard, StoryboardRequest } from "../lib/api";

const GENRES = ["Action", "Horror", "Comedy", "Sci-Fi", "Romance", "Anime", "Documentary"];
const STYLES = ["Hollywood cinematic", "Pixar-like animation", "Anime", "Realistic", "Dark horror", "Documentary"];
const LENGTHS = [15, 30, 60, 120];

export default function Home() {
  const [req, setReq] = useState<StoryboardRequest>({
    idea: "",
    genre: "Sci-Fi",
    length_seconds: 30,
    style: "Hollywood cinematic",
    aspect_ratio: "16:9",
  });
  const [board, setBoard] = useState<Storyboard | null>(null);
  const [busy, setBusy] = useState(false);
  const [busyScene, setBusyScene] = useState<number | null>(null);
  const [error, setError] = useState("");

  const set = <K extends keyof StoryboardRequest>(k: K, v: StoryboardRequest[K]) => setReq((r) => ({ ...r, [k]: v }));

  const withTotal = (b: Storyboard, scenes: Scene[]): Storyboard => ({
    ...b,
    scenes,
    total_seconds: scenes.reduce((a, s) => a + s.duration_seconds, 0),
  });

  async function create() {
    setBusy(true);
    setError("");
    try {
      setBoard(await createStoryboard(req));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  async function regen(scene: Scene) {
    if (!board) return;
    setBusyScene(scene.id);
    setError("");
    try {
      const fresh = await regenerateScene(req, scene);
      setBoard(withTotal(board, board.scenes.map((s) => (s.id === scene.id ? fresh : s))));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Regeneration failed");
    } finally {
      setBusyScene(null);
    }
  }

  function update(id: number, patch: Partial<Scene>) {
    if (!board) return;
    setBoard(withTotal(board, board.scenes.map((s) => (s.id === id ? { ...s, ...patch } : s))));
  }

  function remove(id: number) {
    if (!board) return;
    setBoard(withTotal(board, board.scenes.filter((s) => s.id !== id)));
  }

  function add() {
    if (!board) return;
    const id = Math.max(0, ...board.scenes.map((s) => s.id)) + 1;
    const scene: Scene = {
      id,
      title: "New scene",
      camera: "Medium shot",
      description: "Describe what happens…",
      mood: req.genre,
      duration_seconds: 4,
      video_prompt: "",
    };
    setBoard(withTotal(board, [...board.scenes, scene]));
  }

  return (
    <main>
      <h1>🎬 CineFlow AI</h1>
      <p className="tag">Describe it. Direct it. Create it.</p>

      <section className="panel">
        <label>What do you want to create?</label>
        <textarea
          value={req.idea}
          onChange={(e) => set("idea", e.target.value)}
          placeholder="A funny action movie about a grandfather who accidentally becomes a superhero."
        />
        <div className="row">
          <div>
            <label>Genre</label>
            <select value={req.genre} onChange={(e) => set("genre", e.target.value)}>
              {GENRES.map((g) => <option key={g}>{g}</option>)}
            </select>
          </div>
          <div>
            <label>Length</label>
            <select value={req.length_seconds} onChange={(e) => set("length_seconds", Number(e.target.value))}>
              {LENGTHS.map((l) => <option key={l} value={l}>{l >= 60 ? `${l / 60} min` : `${l} seconds`}</option>)}
            </select>
          </div>
          <div>
            <label>Style</label>
            <select value={req.style} onChange={(e) => set("style", e.target.value)}>
              {STYLES.map((s) => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label>Format</label>
            <select value={req.aspect_ratio} onChange={(e) => set("aspect_ratio", e.target.value as "9:16" | "16:9")}>
              <option value="16:9">YouTube (16:9)</option>
              <option value="9:16">TikTok / Reels / Shorts (9:16)</option>
            </select>
          </div>
        </div>
        <button className="primary" onClick={create} disabled={busy || req.idea.trim().length < 10}>
          {busy ? "Directing…" : "✨ Create storyboard"}
        </button>
        {error && <div className="error">{error}</div>}
      </section>

      {board && (
        <>
          <div className="head">
            <div>
              <h2 style={{ margin: 0 }}>{board.title}</h2>
              <div className="banner">
                {board.logline} · {board.scenes.length} scenes · {board.total_seconds}s · {board.aspect_ratio}
                {board.source === "mock" && " · demo mode (no AI key configured)"}
              </div>
            </div>
            <button onClick={add}>➕ Add scene</button>
          </div>
          <div className="grid">
            {board.scenes.map((s, i) => (
              <article className="panel scene" key={s.id}>
                <div className="meta">SCENE {i + 1} · 📷 {s.camera} · ⏱️ {s.duration_seconds}s</div>
                <input value={s.title} onChange={(e) => update(s.id, { title: e.target.value })} />
                <textarea
                  style={{ marginTop: 8 }}
                  value={s.description}
                  onChange={(e) => update(s.id, { description: e.target.value })}
                />
                <p className="prompt">{s.video_prompt || "Video prompt will be generated."}</p>
                <div className="actions">
                  <button onClick={() => regen(s)} disabled={busyScene === s.id}>
                    {busyScene === s.id ? "…" : "🔄 Regenerate"}
                  </button>
                  <button onClick={() => remove(s.id)}>🗑️ Delete</button>
                </div>
              </article>
            ))}
          </div>
        </>
      )}
    </main>
  );
}
