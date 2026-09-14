import { NextResponse } from "next/server";

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;
const INVALID_EMAIL = "That email doesn’t look right — check it and try again.";
const GENERIC_ERROR = "Couldn’t add you just now — try again.";

export async function POST(request: Request) {
  const apiKey = process.env.KIT_API_KEY;
  const formId = process.env.KIT_FORM_ID;

  if (!apiKey || !formId) {
    return NextResponse.json({ error: GENERIC_ERROR }, { status: 500 });
  }

  let email = "";
  try {
    const body = (await request.json()) as { email?: unknown };
    email = typeof body.email === "string" ? body.email.trim() : "";
  } catch {
    return NextResponse.json({ error: INVALID_EMAIL }, { status: 400 });
  }

  if (!EMAIL_RE.test(email)) {
    return NextResponse.json({ error: INVALID_EMAIL }, { status: 400 });
  }

  const headers = {
    "Content-Type": "application/json",
    "X-Kit-Api-Key": apiKey,
  };

  const createRes = await fetch("https://api.kit.com/v4/subscribers", {
    method: "POST",
    headers,
    body: JSON.stringify({ email_address: email, state: "active" }),
  });

  if (!createRes.ok) {
    const payload = (await createRes.json().catch(() => null)) as {
      errors?: string[];
    } | null;
    const message = payload?.errors?.[0] || GENERIC_ERROR;
    return NextResponse.json({ error: message }, { status: 400 });
  }

  const formRes = await fetch(
    `https://api.kit.com/v4/forms/${formId}/subscribers`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({ email_address: email }),
    },
  );

  if (!formRes.ok) {
    return NextResponse.json({ error: GENERIC_ERROR }, { status: 400 });
  }

  return NextResponse.json({ ok: true });
}
