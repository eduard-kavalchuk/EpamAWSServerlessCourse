import { util } from '@aws-appsync/utils';
import * as ddb from '@aws-appsync/utils/dynamodb';

export function request(ctx) {
    const id = util.autoId();
    const createdAt = util.time.nowISO8601();

    const payload =
        typeof ctx.args.payLoad === 'string'
            ? JSON.parse(ctx.args.payLoad)
            : ctx.args.payLoad;

    return ddb.put({
        key: {
            id
        },
        item: {
            id,
            userId: ctx.args.userId,
            createdAt,
            payLoad: payload
        }
    });
}

export function response(ctx) {
    if (ctx.error) {
        util.error(ctx.error.message, ctx.error.type);
    }

    return {
        id: ctx.result.id,
        createdAt: ctx.result.createdAt
    };
}
