import NextAuth from "next-auth";
import EmailProvider from "next-auth/providers/email";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const handler = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST || "smtp.sendgrid.net",
        port: parseInt(process.env.EMAIL_SERVER_PORT || "587"),
        auth: {
          user: process.env.EMAIL_SERVER_USER || "apikey",
          pass: process.env.EMAIL_SERVER_PASSWORD || "",
        },
      },
      from: process.env.EMAIL_FROM || "noreply@quantview.in",
    }),
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
