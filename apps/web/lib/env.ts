import { z } from "zod";

const envSchema = z.object({
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: z
    .string()
    .optional()
    .default(process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || ""),
  NEXT_PUBLIC_API_URL: z
    .string()
    .optional()
    .transform((val) => (val && val.trim() !== "" ? val : undefined))
    .pipe(z.string().url().optional()),
});

const _env = envSchema.safeParse({
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
});

export const env = _env.success
  ? _env.data
  : {
      NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY:
        process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "",
      NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || undefined,
    };

