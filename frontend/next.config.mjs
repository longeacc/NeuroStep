/** @type {import('next').NextConfig} */
const nextConfig = {
  // Build autonome pour une image Docker légère.
  output: "standalone",
  images: {
    // Les logos/captures du catalogue sont des URLs externes (rendus en `unoptimized`).
    remotePatterns: [{ protocol: "https", hostname: "**" }],
  },
};

export default nextConfig;
