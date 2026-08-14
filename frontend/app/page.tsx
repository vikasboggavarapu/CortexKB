import Image from "next/image";

export default function Home() {
  return (
     <main className="flex min-h-screen items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold">
          RAG Knowledge Base
        </h1>

        <p className="mt-4 text-muted-foreground">
          Search your knowledge base using AI.
        </p>
      </div>
    </main>
  );
}
