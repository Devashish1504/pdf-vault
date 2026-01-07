import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const saveFile = mutation({
    args: {
        userId: v.string(),
        filename: v.string(),
        originalName: v.string(),
        isEncrypted: v.boolean(),
    },
    handler: async (ctx, args) => {
        return await ctx.db.insert("files", {
            userId: args.userId,
            filename: args.filename,
            originalName: args.originalName,
            isEncrypted: args.isEncrypted,
            createdAt: Date.now(),
        });
    },
});

export const getUserFiles = query({
    args: { userId: v.string() },
    handler: async (ctx, args) => {
        return await ctx.db
            .query("files")
            .withIndex("by_user", (q) => q.eq("userId", args.userId))
            .collect();
    },
});

export const getFileById = query({
    args: { fileId: v.id("files") },
    handler: async (ctx, args) => {
        return await ctx.db.get(args.fileId);
    },
});

export const deleteFile = mutation({
    args: { fileId: v.id("files") },
    handler: async (ctx, args) => {
        await ctx.db.delete(args.fileId);
    },
});
