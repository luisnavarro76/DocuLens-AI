"use client";

import { useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Brain } from "lucide-react";
import Link from "next/link";
import GoogleSignInButton from "@/components/auth/GoogleSignInButton";
import { PasswordField } from "@/components/auth/PasswordField";
import { isPasswordValid } from "@/lib/password-validation";

export default function RegisterPage() {
  const { register } = useAuth();
  const { t } = useTranslation();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const passwordValid = isPasswordValid(password);
  const canSubmit = username.trim().length >= 3 && email.trim().length > 0 && passwordValid && !loading;

  const handleGoogleSuccess = useCallback(() => {
    router.replace("/dashboard");
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!passwordValid) {
      setError(t("password.invalidSubmit"));
      return;
    }

    setLoading(true);

    try {
      await register(username, email, password);
      router.replace("/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : t("register.fallbackError");
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[500px] h-[300px] bg-primary/8 rounded-full blur-[100px] pointer-events-none" />

      <Card className="w-full max-w-md relative z-10 bg-card/80 backdrop-blur-xl border-border/50 animate-fade-in-up">
        <CardHeader className="text-center pb-2">
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 rounded-xl bg-primary/15 flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold">{t("register.title")}</CardTitle>
          <CardDescription>{t("register.description")}</CardDescription>
        </CardHeader>

        <CardContent>
          <div className="mb-4">
            <GoogleSignInButton
              onError={setError}
              onSuccess={handleGoogleSuccess}
            />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            {error && (
              <div
                role="alert"
                className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-sm text-destructive"
              >
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label htmlFor="reg-username" className="text-sm font-medium">
                {t("common.username")}
              </label>
              <Input
                id="reg-username"
                type="text"
                placeholder="paramjit"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                minLength={3}
                className="h-11"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="reg-email" className="text-sm font-medium">
                {t("common.email")}
              </label>
              <Input
                id="reg-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="h-11"
              />
            </div>

            <PasswordField
              id="reg-password"
              value={password}
              onChange={setPassword}
              placeholder={t("register.passwordPlaceholder")}
            />

            <Button
              type="submit"
              className="w-full h-11 text-base"
              disabled={!canSubmit}
              aria-disabled={!canSubmit}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                  {t("register.submitting")}
                </span>
              ) : (
                t("register.submit")
              )}
            </Button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            {t("register.hasAccount")}{" "}
            <Link href="/login" className="text-primary hover:underline font-medium">
              {t("register.signIn")}
            </Link>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
