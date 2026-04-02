/** @type {import('next').NextConfig} */
const backendUrl = (
  process.env.API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:7860"
).replace(/\/$/, "");

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: "/download/:path*",
        destination: `${backendUrl}/download/:path*`,
      },
    ];
  },
};

export default nextConfig;
