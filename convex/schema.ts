import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    clerkId: v.string(),
    email: v.string(),
    name: v.optional(v.string()),
    createdAt: v.number(),
  }).index("by_clerk_id", ["clerkId"]),

  files: defineTable({
    userId: v.string(),
    filename: v.string(),
    originalName: v.string(),
    isEncrypted: v.boolean(),
    createdAt: v.number(),
  }).index("by_user", ["userId"]),
});
