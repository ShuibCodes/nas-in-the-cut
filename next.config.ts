import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The landing page is the static build from nas-new/, published into
  // public/ by nas-new/tools/publish-next.sh.
  async rewrites() {
    return {
      beforeFiles: [
        { source: "/", destination: "/index.html" },
        { source: "/newsletter", destination: "/index.html" },
        { source: "/in-the-room", destination: "/in-the-room.html" },
        { source: "/in-the-cup", destination: "/in-the-cup.html" },
      ],
    };
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
      {
        source: "/:dir(assets|img)/:path*",
        headers: [
          {
            key: "Cache-Control",
            value: "public, max-age=31536000, immutable",
          },
        ],
      },
    ];
  },
};

export default nextConfig;
