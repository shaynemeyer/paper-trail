import { expect, test, type Page } from 'playwright/test'

const documentFixture = {
  id: 1,
  name: 'Test Document',
  description: 'Browser acceptance fixture',
  doctype: 'pdf',
  document_source: null,
  status: 'approved',
  raw_url: null,
  markdown_url: null,
  created_at: '2026-09-04T12:00:00Z',
  updated_at: '2026-09-04T12:00:00Z',
}

async function openDocumentChat(page: Page) {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: 'Your Documents' })).toBeVisible()
  await page.getByRole('button', { name: 'Chat', exact: true }).click()
  await expect(
    page.getByRole('heading', { name: 'Chat with Test Document' }),
  ).toBeVisible()
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    const payload = btoa(JSON.stringify({ sub: 'test-user', role: 'user' }))
      .replace(/=/g, '')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
    localStorage.setItem('pt_token', `test.${payload}.signature`)
  })

  await page.route('**/api/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([documentFixture]),
    })
  })
})

test('submits a question, renders the answer, and resets after reselection', async ({
  page,
}) => {
  const chatRequests: Array<{ method: string; authorization: string | undefined; body: unknown }> = []
  await page.route('**/api/documents/1/chat', async (route) => {
    chatRequests.push({
      method: route.request().method(),
      authorization: route.request().headers().authorization,
      body: route.request().postDataJSON(),
    })
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ answer: 'Grounded answer', chunk_ids: [7, 9] }),
    })
  })

  await openDocumentChat(page)
  await page
    .getByRole('textbox', { name: 'Question about Test Document' })
    .fill('What does this document say?')
  await page.getByRole('button', { name: 'Ask question' }).click()

  await expect(page.getByText('Grounded answer', { exact: true })).toBeVisible()
  expect(chatRequests).toEqual([
    {
      method: 'POST',
      authorization: expect.stringMatching(/^Bearer /),
      body: { message: 'What does this document say?' },
    },
  ])

  await page.getByRole('button', { name: 'Close', exact: true }).click()
  await page.getByRole('button', { name: 'Chat', exact: true }).click()

  await expect(
    page.getByText('Ask a question about Test Document to start the conversation.'),
  ).toBeVisible()
  await expect(page.getByText('Grounded answer', { exact: true })).toHaveCount(0)
})

test('blocks blank questions and shows API error details', async ({ page }) => {
  const chatMessages: string[] = []
  await page.route('**/api/documents/1/chat', async (route) => {
    const body = route.request().postDataJSON() as { message: string }
    chatMessages.push(body.message)
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({
        detail: 'Document not found or has no embedded chunks yet',
      }),
    })
  })

  await openDocumentChat(page)
  const input = page.getByRole('textbox', { name: 'Question about Test Document' })

  await input.fill('   ')
  await page.getByRole('button', { name: 'Ask question' }).click()
  await expect(page.getByText('Enter a question.', { exact: true })).toBeVisible()
  expect(chatMessages).toEqual([])

  await input.fill('Trigger missing chunks')
  await page.getByRole('button', { name: 'Ask question' }).click()
  await expect(
    page.getByText('Document not found or has no embedded chunks yet', { exact: true }),
  ).toBeVisible()
  expect(chatMessages).toEqual(['Trigger missing chunks'])
})


test('keeps the latest answer visible after the transcript overflows', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 480 })
  let responseNumber = 0

  await page.route('**/api/documents/1/chat', async (route) => {
    responseNumber += 1
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        answer: `Grounded answer ${responseNumber}: ${'Supporting context. '.repeat(8)}`,
        chunk_ids: [responseNumber],
      }),
    })
  })

  await openDocumentChat(page)
  const input = page.getByRole('textbox', { name: 'Question about Test Document' })

  for (let questionNumber = 1; questionNumber <= 8; questionNumber += 1) {
    await input.fill(`Question ${questionNumber}`)
    await page.getByRole('button', { name: 'Ask question' }).click()
    await expect(page.getByText(new RegExp(`^Grounded answer ${questionNumber}:`))).toBeVisible()
  }

  const transcript = page.getByRole('log')
  const latestAnswer = page.getByText(/^Grounded answer 8:/)

  await expect.poll(() => transcript.evaluate((element) => element.scrollTop)).toBeGreaterThan(0)
  await expect(latestAnswer).toBeInViewport()
})
