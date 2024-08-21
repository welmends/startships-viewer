"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_BASE_URL } from "./constants";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const access_token = localStorage.getItem("access_token");

    if (!access_token) {
      router.push("/login");
      return;
    }

    fetch(`${API_BASE_URL}/api/ping`, {
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
