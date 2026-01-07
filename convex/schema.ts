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
    storageId: v.optional(v.id("_storage")),
    isEncrypted: v.boolean(),
    encryptedStorageId: v.optional(v.id("_storage")),
    createdAt: v.number(),
  }).index("by_user", ["userId"]),
});
