import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return <SignIn appearance={{ elements: { formButtonPrimary: "bg-indigo-600 hover:bg-indigo-500" } }} />;
}
