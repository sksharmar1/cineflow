export type Scene = {
  id: number;
  title: string;
  camera: string;
  description: string;
  mood: string;
  duration_seconds: number;
  video_prompt: string;
};

export type StoryboardRequest = {
  idea: string;
  genre: string;
  length_seconds: number;
  style: string;
  aspect_ratio: "9:16" | "16:9";
};

export type Storyboard = {
  title: string;
  logline: string;
  style: string;
  aspect_ratio: "9:16" | "16:9";
  scenes: Scene[];
  total_seconds: number;
  source: "ai" | "mock";
};

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = typeof j.detail === "string" ? j.detail : JSON.stringify(j.detail);
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export const createStoryboard = (req: StoryboardRequest) => post<Storyboard>("/api/storyboard", req);
export const regenerateScene = (request: StoryboardRequest, scene: Scene, instruction?: string) =>
  post<Scene>("/api/scene/regenerate", { request, scene, instruction });
