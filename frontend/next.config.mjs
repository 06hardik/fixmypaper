/** @type {import('next').NextConfig} */
const backendUrl = (
  "http://backend:7860"
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
