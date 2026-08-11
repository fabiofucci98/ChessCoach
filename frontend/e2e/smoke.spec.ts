import { expect, test } from "@playwright/test";

// Smoke test: the app shell renders. Requires the full stack (web + api + db)
// and a browser installed via `npx playwright install`.
test("home page renders the app shell", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByText(/ChessCoach|Login|Register|Play vs Stockfish/).first()
  ).toBeVisible();
});
