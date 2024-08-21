"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
      router.push("/login");
      return;
    }

    fetch("http://0.0.0.0:8000/api/ping", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${access_token}`,
      },
    })
      .then((res) => {
        if (!res.ok) {
          router.push("/login");
        } else {
          router.push("/dashboard");
        }
      })
      .catch(() => {
        router.push("/login");
      });
  }, [router]);

  return null;
}
