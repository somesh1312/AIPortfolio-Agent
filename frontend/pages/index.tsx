import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/chat"); // instantly redirect
  }, [router]);

  return null; // nothing shows, just redirects
}