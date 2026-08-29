/// <reference types="@testing-library/jest-dom" />
import { describe, it, expect } from "vitest";
import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import { EmptyState } from "../components/shared/EmptyState";

describe("EmptyState Component", () => {
  it("renders the default title and description", () => {
    render(<EmptyState />);
    expect(screen.getByText("No data found")).toBeInTheDocument();
    expect(
      screen.getByText("Get started by creating a new entry."),
    ).toBeInTheDocument();
  });

  it("renders custom title and description", () => {
    render(
      <EmptyState title="Custom Title" description="Custom Description" />,
    );
    expect(screen.getByText("Custom Title")).toBeInTheDocument();
    expect(screen.getByText("Custom Description")).toBeInTheDocument();
  });
});
