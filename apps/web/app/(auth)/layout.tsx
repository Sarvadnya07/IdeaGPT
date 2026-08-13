export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="flex min-h-dvh items-center justify-center bg-[#070709] p-4">
      {children}
    </main>
  );
}
