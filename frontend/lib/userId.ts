export function getUserId(): string {
  if (typeof window === "undefined") return "ssr-user";
  let id = localStorage.getItem("clipper_user_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("clipper_user_id", id);
  }
  return id;
}
