import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { WordbookEditor } from "../src/wordbook/WordbookEditor";
import type { LearningItem } from "../src/types";

const item: LearningItem = {
  id: 1,
  original_text: "Erfahrung",
  translation: "experience",
  item_type: "word",
  status: "learning",
  article: "die",
  notes: "Useful",
  created_at: "2026-01-01T00:00:00Z",
  occurrences: [],
  flashcards: [],
};

test("submits edited translation and grammar fields", async () => {
  const onSave = vi.fn().mockResolvedValue(undefined);
  render(<WordbookEditor item={item} onSave={onSave} />);

  fireEvent.change(screen.getByLabelText("Translation"), { target: { value: "practical experience" } });
  fireEvent.change(screen.getByLabelText("Plural"), { target: { value: "Erfahrungen" } });
  fireEvent.change(screen.getByLabelText("Required case"), { target: { value: "Akkusativ" } });
  fireEvent.click(screen.getByLabelText("Separable"));
  fireEvent.click(screen.getByRole("button", { name: "Save changes" }));

  await waitFor(() => expect(onSave).toHaveBeenCalledWith(expect.objectContaining({
    translation: "practical experience",
    plural: "Erfahrungen",
    required_case: "Akkusativ",
    separable: true,
  })));
  expect(screen.getByRole("status")).toHaveTextContent("Changes saved locally.");
});

test("sends cleared optional fields as null", async () => {
  const onSave = vi.fn().mockResolvedValue(undefined);
  render(<WordbookEditor item={item} onSave={onSave} />);
  fireEvent.change(screen.getByLabelText("Article"), { target: { value: "   " } });
  fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
  await waitFor(() => expect(onSave).toHaveBeenCalledWith(expect.objectContaining({ article: null })));
});

test("shows a useful error when saving fails", async () => {
  const onSave = vi.fn().mockRejectedValue(new Error("Local service is unavailable."));
  render(<WordbookEditor item={item} onSave={onSave} />);
  fireEvent.click(screen.getByRole("button", { name: "Save changes" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("Local service is unavailable.");
  expect(screen.getByRole("button", { name: "Save changes" })).toBeEnabled();
});
