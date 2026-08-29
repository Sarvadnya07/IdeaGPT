/** @type {import('next').NextConfig} */
import bundleAnalyzer from "@next/bundle-analyzer";

const withBundleAnalyzer = bundleAnalyzer({
  enabled: process.env.ANALYZE === "true",
});

const isDev = process.env.NODE_ENV !== "production";

const scriptSrc = [
  "'self'",
  "'unsafe-inline'",
  ...(isDev ? ["'unsafe-eval'"] : []),
  "https://clerk.ideagpt.com",
  "https://*.clerk.accounts.dev",
  "https://challenges.cloudflare.com",
].join(" ");

const apiUrl = process.env.NEXT_PUBLIC_API_URL;

const devOrigins = isDev
  ? [
      "http://localhost:8000",
      "http://127.0.0.1:8000",
      "http://localhost:3000",
      "http://127.0.0.1:3000",
    ]
  : [];

const connectSrc = [
  "'self'",
  ...devOrigins,
  "https://*.clerk.accounts.dev",
  "https://api.clerk.com",
  "https://clerk.ideagpt.com",
  "https://*.clerk.com",
  "https://clerk-telemetry.com",
  "https://*.clerk-telemetry.com",
  "wss://*.clerk.accounts.dev",
  "https://*.ideagpt.com",
  "https://*.ideagpt.dev",
  "https://*.vercel.app",
  ...(apiUrl ? [apiUrl] : []),
].join(" ");

const nextConfig = {
  output: process.env.BUILD_STANDALONE === "true" || process.env.DOCKER_BUILD === "true" ? "standalone" : undefined,
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value:
              "camera=(), microphone=(), geolocation=(), interest-cohort=()",
          },
          {
            key: "Strict-Transport-Security",
            value: "max-age=63072000; includeSubDomains; preload",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              `script-src ${scriptSrc}`,
              "worker-src 'self' blob:",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob: https:",
              "font-src 'self' data:",
              `connect-src ${connectSrc}`,
              "frame-src 'self' https://*.clerk.accounts.dev https://clerk.ideagpt.com https://*.clerk.com https://challenges.cloudflare.com",
              "object-src 'none'",
              "base-uri 'self'",
              "form-action 'self'",
            ].join("; "),
          },
        ],
      },
    ];
  },
  async rewrites() {
    const backendUrl = process.env.INTERNAL_API_URL || process.env.FASTAPI_URL;
    if (backendUrl) {
      return [
        {
          source: "/api/v1/:path*",
          destination: `${backendUrl.replace(/\/$/, "")}/api/v1/:path*`,
        },
      ];
    }
    return [];
  },
};

export default withBundleAnalyzer(nextConfig);
