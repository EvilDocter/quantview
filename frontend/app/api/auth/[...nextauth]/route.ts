import NextAuth from "next-auth";
import EmailProvider from "next-auth/providers/email";
import CredentialsProvider from "next-auth/providers/credentials";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const handler = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    EmailProvider({
      async sendVerificationRequest({ identifier: email, url, provider: { from } }) {
        const apiKey = process.env.EMAIL_SERVER_PASSWORD;
        if (!apiKey || apiKey === "YOUR_SENDGRID_API_KEY") {
          console.warn("SendGrid API Key is not set or is using placeholder. Falling back to log-only.");
          console.log(`[Magic Link Auth] Magic link for ${email}: ${url}`);
          return;
        }

        const response = await fetch("https://api.sendgrid.com/v3/mail/send", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${apiKey}`,
          },
          body: JSON.stringify({
            personalizations: [
              {
                to: [{ email }],
                subject: "Sign in to QuantView",
              },
            ],
            from: { email: from },
            content: [
              {
                type: "text/html",
                value: `
                  <div style="background-color: #0b1120; color: #f8fafc; padding: 40px; font-family: sans-serif; text-align: center; border-radius: 20px; max-width: 500px; margin: 0 auto; border: 1px solid #1e293b;">
                    <h1 style="color: #a855f7; font-size: 24px; font-weight: 800; margin-bottom: 24px;">QuantView Terminal</h1>
                    <p style="font-size: 14px; color: #94a3b8; margin-bottom: 30px;">Click the button below to sign in securely to your QuantView account.</p>
                    <a href="${url}" style="background-color: #9333ea; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 12px; font-weight: bold; font-size: 14px; display: inline-block; box-shadow: 0 0 20px rgba(168, 85, 247, 0.4);">Access Terminal</a>
                    <p style="font-size: 11px; color: #64748b; margin-top: 35px;">If you did not request this link, you can safely ignore this email.</p>
                  </div>
                `,
              },
            ],
          }),
        });

        if (!response.ok) {
          const errorText = await response.text();
          console.error("SendGrid API error:", errorText);
          throw new Error("Failed to send verification email via SendGrid API");
        }
      },
      from: process.env.EMAIL_FROM || "noreply@quantview.in",
    }),
    CredentialsProvider({
      name: "Demo Account",
      credentials: {
        email: { label: "Email", type: "email", placeholder: "you@example.com" }
      },
      async authorize(credentials) {
        if (credentials?.email) {
          return {
            id: credentials.email,
            email: credentials.email,
            name: credentials.email.split("@")[0]
          };
        }
        return null;
      }
    })
  ],
  secret: process.env.NEXTAUTH_SECRET || "some-long-secret-key-quantview",
  session: {
    strategy: "jwt",
  },
  callbacks: {
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.sub;
      }
      return session;
    },
  },
});

export { handler as GET, handler as POST };
