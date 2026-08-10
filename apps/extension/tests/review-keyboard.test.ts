import { reviewAction } from "../src/review/keyboard";

test("review shortcuts reveal and grade outside fields", () => {
  expect(reviewAction({ key: " ", code: "Space", target: document.body }, false)).toBe("reveal");
  expect(reviewAction({ key: "3", code: "Digit3", target: document.body }, true)).toBe("good");
});

test("does not grade while user is typing", () => {
  const input = document.createElement("input");
  expect(reviewAction({ key: "3", code: "Digit3", target: input }, true)).toBeNull();
  expect(reviewAction({ key: "Enter", code: "Enter", target: input }, false)).toBe("reveal");
});

