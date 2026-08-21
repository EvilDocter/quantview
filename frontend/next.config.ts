import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    // On the IIT server, backend runs on port 8001 on the same host
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";
    return [
      {
        source: "/api/v1/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || "",
    NEXT_PUBLIC_BACKEND_URL_INDIA: process.env.NEXT_PUBLIC_BACKEND_URL_INDIA || "",
  },
};

export default nextConfig;

