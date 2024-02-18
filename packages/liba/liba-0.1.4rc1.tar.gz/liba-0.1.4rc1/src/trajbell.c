#include "a/trajbell.h"
#include "a/math.h"

a_float a_trajbell_gen(a_trajbell *ctx, a_float jm, a_float am, a_float vm,
                       a_float q0, a_float q1, a_float v0, a_float v1)
{
    a_float tj, v02, v12, _2v0, _2v1, _2am, v0v1, Am2_Jm;
    a_float const q = q1 - q0;
    if (jm < 0) { jm = -jm; }
    if (am < 0) { am = -am; }
    if (vm < 0) { vm = -vm; }
    if (v0 < -vm) { v0 = -vm; }
    else if (v0 > vm) { v0 = vm; }
    if (v1 < -vm) { v1 = -vm; }
    else if (v1 > vm) { v1 = vm; }
    if (q < 0)
    {
        jm = -jm;
        am = -am;
        vm = -vm;
    }
    ctx->q0 = q0;
    ctx->q1 = q1;
    ctx->v0 = v0;
    ctx->v1 = v1;
    ctx->vm = vm;
    ctx->jm = jm;
    _2am = am * am;
    _2v0 = vm - v0;
    if (_2v0 * jm < _2am)
    {
        ctx->taj = a_float_sqrt(_2v0 / jm);
        ctx->ta = 2 * ctx->taj;
        ctx->am = +jm * ctx->taj;
    }
    else
    {
        ctx->taj = am / jm;
        ctx->ta = ctx->taj + _2v0 / am;
        ctx->am = +am;
    }
    _2v1 = vm - v1;
    if (_2v1 * jm < _2am)
    {
        ctx->tdj = a_float_sqrt(_2v1 / jm);
        ctx->td = 2 * ctx->tdj;
        ctx->dm = -jm * ctx->tdj;
    }
    else
    {
        ctx->tdj = am / jm;
        ctx->td = ctx->tdj + _2v1 / am;
        ctx->dm = -am;
    }
    ctx->tv = q / vm - A_FLOAT_C(0.5) * ctx->ta * (1 + v0 / vm) - A_FLOAT_C(0.5) * ctx->td * (1 + v1 / vm);
    if (ctx->tv > 0) { goto out; }
    ctx->tv = 0;
    v02 = v0 * v0;
    v12 = v1 * v1;
    _2v0 = 2 * v0;
    _2v1 = 2 * v1;
    v0v1 = v0 + v1;
    do {
        tj = am / jm;
        _2am = 2 * am;
        ctx->taj = tj;
        ctx->tdj = tj;
        Am2_Jm = am * tj;
        Am2_Jm += a_float_sqrt(Am2_Jm * Am2_Jm + 2 * (v02 + v12) + (4 * q - 2 * v0v1 * tj) * am);
        ctx->ta = (Am2_Jm - _2v0) / _2am;
        ctx->td = (Am2_Jm - _2v1) / _2am;
        if (ctx->ta < 0)
        {
            ctx->ta = 0;
            ctx->taj = 0;
            ctx->td = 2 * q / v0v1;
            ctx->tdj = (jm * q - a_float_sqrt((jm + q * q + (v1 - v0) * v0v1 * v0v1) * jm)) / (v0v1 * jm);
            ctx->am = 0;
            ctx->dm = -jm * ctx->tdj;
            ctx->vm = v0;
            goto out;
        }
        if (ctx->td < 0)
        {
            ctx->td = 0;
            ctx->tdj = 0;
            ctx->ta = 2 * q / v0v1;
            ctx->taj = (jm * q - a_float_sqrt((jm + q * q + (v0 - v1) * v0v1 * v0v1) * jm)) / (v0v1 * jm);
            ctx->am = +jm * ctx->taj;
            ctx->dm = 0;
            ctx->vm = v0 + ctx->am * (ctx->ta - ctx->taj);
            goto out;
        }
        _2am = 2 * tj;
        if (ctx->ta >= _2am && ctx->td >= _2am)
        {
            ctx->am = +am;
            ctx->dm = -am;
            ctx->vm = v0 + ctx->am * (ctx->ta - tj);
            goto out;
        }
        am *= A_FLOAT_C(0.5);
    } while ((am < 0 ? -am : am) > A_FLOAT_C(0.01));
    ctx->am = 0;
    ctx->t = 0;
    return 0;
out:
    ctx->t = ctx->ta + ctx->tv + ctx->td;
    return ctx->t;
}

a_float a_trajbell_pos(a_trajbell const *ctx, a_float dt)
{
    if (dt < ctx->ta)
    {
        if (dt < ctx->taj)
        {
            if (dt <= 0) { return ctx->q0; }
            return ctx->q0 + ctx->v0 * dt + ctx->jm * dt * dt * dt / 6;
        }
        if (dt < ctx->ta - ctx->taj)
        {
            return ctx->q0 + ctx->v0 * dt + ctx->am * (3 * dt * dt - 3 * dt * ctx->taj + ctx->taj * ctx->taj) / 6;
        }
        dt = ctx->ta - dt;
        return ctx->q0 + A_FLOAT_C(0.5) * (ctx->vm + ctx->v0) * ctx->ta - ctx->vm * dt + ctx->jm * dt * dt * dt / 6;
    }
    if (dt < ctx->t - ctx->td + ctx->tdj)
    {
        if (dt < ctx->ta + ctx->tv)
        {
            return ctx->q0 + A_FLOAT_C(0.5) * (ctx->vm + ctx->v0) * ctx->ta + ctx->vm * (dt - ctx->ta);
        }
        dt -= ctx->t - ctx->td;
        return ctx->q1 - A_FLOAT_C(0.5) * (ctx->vm + ctx->v1) * ctx->td + ctx->vm * dt - ctx->jm * dt * dt * dt / 6;
    }
    if (dt < ctx->t)
    {
        if (dt < ctx->t - ctx->tdj)
        {
            dt -= ctx->t - ctx->td;
            return ctx->q1 - A_FLOAT_C(0.5) * (ctx->vm + ctx->v1) * ctx->td + ctx->vm * dt +
                   ctx->dm * (3 * dt * dt - 3 * dt * ctx->tdj + ctx->tdj * ctx->tdj) / 6;
        }
        dt = ctx->t - dt;
        return ctx->q1 - ctx->v1 * dt - ctx->jm * dt * dt * dt / 6;
    }
    return ctx->q1;
}

a_float a_trajbell_vel(a_trajbell const *ctx, a_float dt)
{
    if (dt < ctx->ta)
    {
        if (dt < ctx->taj)
        {
            if (dt <= 0) { return ctx->v0; }
            return ctx->v0 + A_FLOAT_C(0.5) * ctx->jm * dt * dt;
        }
        if (dt < ctx->ta - ctx->taj)
        {
            return ctx->v0 + ctx->am * (dt - A_FLOAT_C(0.5) * ctx->taj);
        }
        dt = ctx->ta - dt;
        return ctx->vm - A_FLOAT_C(0.5) * ctx->jm * dt * dt;
    }
    if (dt < ctx->t - ctx->td + ctx->tdj)
    {
        if (dt < ctx->ta + ctx->tv) { return ctx->vm; }
        dt -= ctx->t - ctx->td;
        return ctx->vm - A_FLOAT_C(0.5) * ctx->jm * dt * dt;
    }
    if (dt < ctx->t)
    {
        if (dt < ctx->t - ctx->tdj)
        {
            return ctx->vm + ctx->dm * (dt - ctx->t + ctx->td - A_FLOAT_C(0.5) * ctx->tdj);
        }
        dt = ctx->t - dt;
        return ctx->v1 + A_FLOAT_C(0.5) * ctx->jm * dt * dt;
    }
    return ctx->v1;
}

a_float a_trajbell_acc(a_trajbell const *ctx, a_float dt)
{
    if (dt < ctx->ta)
    {
        if (dt >= ctx->taj)
        {
            if (dt < ctx->ta - ctx->taj) { return ctx->am; }
            return ctx->jm * (ctx->ta - dt);
        }
        if (dt > 0) { return ctx->jm * dt; }
    }
    else if (dt < ctx->t - ctx->td + ctx->tdj)
    {
        if (dt >= ctx->ta + ctx->tv)
        {
            return -ctx->jm * (dt - ctx->t + ctx->td);
        }
    }
    else if (dt < ctx->t)
    {
        if (dt < ctx->t - ctx->tdj) { return ctx->dm; }
        return -ctx->jm * (ctx->t - dt);
    }
    return 0;
}

a_float a_trajbell_jer(a_trajbell const *ctx, a_float dt)
{
    if (dt < ctx->ta)
    {
        if (dt >= ctx->ta - ctx->taj)
        {
            return -ctx->jm;
        }
        if (dt < ctx->taj && dt >= 0)
        {
            return +ctx->jm;
        }
    }
    else if (dt < ctx->t - ctx->td + ctx->tdj)
    {
        if (dt >= ctx->ta + ctx->tv)
        {
            return -ctx->jm;
        }
    }
    else if (dt <= ctx->t)
    {
        if (dt >= ctx->t - ctx->tdj)
        {
            return +ctx->jm;
        }
    }
    return 0;
}
