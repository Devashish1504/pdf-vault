import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const generateUploadUrl = mutation({
    args: {},
    handler: async (ctx) => {
        return await ctx.storage.generateUploadUrl();
    },
});

export const saveFile = mutation({
    args: {
        userId: v.string(),
        filename: v.string(),
        originalName: v.string(),
        storageId: v.id("_storage"),
        isEncrypted: v.boolean(),
    },
    handler: async (ctx, args) => {
        return await ctx.db.insert("files", {
            userId: args.userId,
            filename: args.filename,
            originalName: args.originalName,
            storageId: args.storageId,
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

export const updateFileEncrypted = mutation({
    args: {
        fileId: v.id("files"),
        encryptedStorageId: v.id("_storage"),
    },
    handler: async (ctx, args) => {
        await ctx.db.patch(args.fileId, {
            isEncrypted: true,
            encryptedStorageId: args.encryptedStorageId,
        });
    },
});

export const deleteFile = mutation({
    args: { fileId: v.id("files") },
    handler: async (ctx, args) => {
        const file = await ctx.db.get(args.fileId);
        if (file?.storageId) {
            await ctx.storage.delete(file.storageId);
        }
        if (file?.encryptedStorageId) {
            await ctx.storage.delete(file.encryptedStorageId);
        }
        await ctx.db.delete(args.fileId);
    },
});

export const getFileUrl = query({
    args: { storageId: v.id("_storage") },
    handler: async (ctx, args) => {
        return await ctx.storage.getUrl(args.storageId);
    },
});
