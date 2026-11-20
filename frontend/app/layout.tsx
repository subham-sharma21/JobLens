import "./globals.css";
import Header from "@/components/Header";
import { ThemeProvider } from "@/components/ThemeProvider";

export const metadata = {
  title: "JobLens 2.0 — Geospatial Tech Job Market Intelligence",
  description: "Enterprise labor market intelligence, ATS job tracking, and geospatial hiring demand analytics.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var theme = localStorage.getItem('joblens-theme');
                  if (theme === 'light') {
                    document.documentElement.classList.remove('dark');
                  } else {
                    document.documentElement.classList.add('dark');
                  }
                } catch (e) {
                  document.documentElement.classList.add('dark');
                }
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 antialiased transition-colors duration-200">
        <ThemeProvider>
          <Header />
          <main className="flex-1">{children}</main>
          <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-6 text-center text-xs text-slate-500 dark:text-slate-400 transition-colors duration-200">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div>
                <strong className="text-slate-800 dark:text-slate-200">JobLens 2.0</strong> — Built with Next.js, FastAPI, PostgreSQL & Direct ATS Crawlers
              </div>
              <div className="flex items-center gap-4 text-slate-400 dark:text-slate-500">
                <span>Direct Greenhouse & Lever Ingestion</span>
                <span>•</span>
                <span>Updated in Real Time</span>
              </div>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
