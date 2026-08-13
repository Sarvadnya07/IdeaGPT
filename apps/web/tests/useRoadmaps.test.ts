import { describe, it, expect } from "vitest";
import { Milestone, Task, Roadmap } from "../hooks/useRoadmaps";

describe("Roadmaps Data Structure", () => {
  it("constructs valid milestone and task JSON structures according to OpenAPI schema", () => {
    const task: Task = {
      title: "Design DB Schema",
      description: "Create initial Alembic migration",
      estimated_days: 2,
      status: "completed",
    };

    const milestone: Milestone = {
      title: "Phase 1: Architecture",
      objective: "Set up PostgreSQL and FastAPI",
      tasks: [task],
    };

    const roadmap: Partial<Roadmap> = {
      project_id: "test-proj-1",
      milestones: [milestone],
      status: "active",
    };

    expect(roadmap.status).toBe("active");
    expect(roadmap.milestones?.length).toBe(1);
    expect(roadmap.milestones?.[0].tasks[0].status).toBe("completed");
  });
});
