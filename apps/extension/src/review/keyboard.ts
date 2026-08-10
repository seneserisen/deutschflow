export type ReviewAction = "reveal" | "again" | "hard" | "good" | "easy" | null;

export function reviewAction(event: Pick<KeyboardEvent, "key" | "code" | "target">, revealed: boolean): ReviewAction {
  const element = event.target as HTMLElement | null;
  const tag = element?.tagName ?? "";
  const typing = ["INPUT", "TEXTAREA", "SELECT"].includes(tag);
  if (event.key === "Enter" && tag === "INPUT") return "reveal";
  if (typing) return null;
  if (event.code === "Space") return "reveal";
  if (revealed) return ({ "1": "again", "2": "hard", "3": "good", "4": "easy" } as const)[event.key as "1"] ?? null;
  return null;
}

