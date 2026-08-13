import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <SignIn
      fallbackRedirectUrl="/dashboard"
      appearance={{
        variables: {
          colorBackground: "#0c0c0e",
          colorText: "#f4f4f5",
          colorPrimary: "#4f46e5",
          colorInputBackground: "#070709",
          colorInputText: "#f4f4f5",
        },
        elements: {
          cardBox: "shadow-2xl shadow-black/40",
          formButtonPrimary: "bg-indigo-600 hover:bg-indigo-500",
        },
      }}
    />
  );
}
