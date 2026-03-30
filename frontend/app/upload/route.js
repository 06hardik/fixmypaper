import { NextResponse } from "next/server";

export const runtime = "nodejs";

/**
 * Proxies the multipart upload to Flask.
 * This avoids Next's rewrite proxy instability/timeouts during long PDF processing.
 */
export async function POST(request) {
  const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001";

  // Parse multipart from the client.
  const incoming = await request.formData();

  const fd = new FormData();
  const file = incoming.get("file");
  if (file) {
    // Ensure we proxy as a Blob/FiIe to keep the multipart structure intact.
    const buf = await file.arrayBuffer();
    const blob = new Blob([buf], { type: file.type || "application/pdf" });
    fd.append("file", blob, file.name || "upload.pdf");
  }

  const formatId = incoming.get("format_id");
  if (formatId) fd.append("format_id", formatId);

  const startPage = incoming.get("start_page");
  if (startPage) fd.append("start_page", startPage);

  const controller = new AbortController();
  const timeoutMs = 180000; // 3 minutes; adjust if your pipeline can take longer.
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const backendRes = await fetch(`${API}/upload`, {
      method: "POST",
      body: fd,
      signal: controller.signal,
    });

    // Return backend response as-is.
    const contentType = backendRes.headers.get("content-type");
    const body = await backendRes.arrayBuffer();
    return new NextResponse(body, {
      status: backendRes.status,
      headers: contentType ? { "content-type": contentType } : undefined,
    });
  } finally {
    clearTimeout(timeout);
  }
}

