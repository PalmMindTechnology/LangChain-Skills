import { NextRequest, NextResponse } from "next/server";

const BACKEND = process.env.API_URL ?? "http://localhost:8089";

async function proxy(req: NextRequest, { params }: { params: { path: string[] } }) {
  const path = params.path.join("/");
  const url = `${BACKEND}/${path}`;

  let body: string | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.text();
  }

  const upstream = await fetch(url, {
    method: req.method,
    headers: { "Content-Type": "application/json" },
    body,
    duplex: "half",
  } as RequestInit);

  if (upstream.headers.get("content-type")?.includes("text/event-stream")) {
    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Thread-Id": upstream.headers.get("X-Thread-Id") ?? "",
      },
    });
  }

  const data = await upstream.json().catch(() => ({}));
  return NextResponse.json(data, { status: upstream.status });
}

export const GET     = proxy;
export const POST    = proxy;
export const PUT     = proxy;
export const DELETE  = proxy;
export const OPTIONS = proxy;
export const dynamic = "force-dynamic";