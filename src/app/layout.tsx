import type { ReactNode } from 'react';

export const metadata = {
  title: 'RealSTEM',
  description: 'News-to-lesson AI generator for teachers and students.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}