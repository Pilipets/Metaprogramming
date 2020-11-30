package io.reactivex.rxjava3.core;

import java.util.*;
import java.util.concurrent.TimeUnit;

import org.openjdk.jmh.annotations.*;
import org.openjdk.jmh.infra.Blackhole;
import org.reactivestreams.Publisher;

import io.reactivex.rxjava3.functions.Function;

@BenchmarkMode(Mode.Throughput)
@Warmup(iterations = 5)
@Measurement(iterations = 5, time = 5, timeUnit = TimeUnit.SECONDS)
@OutputTimeUnit(TimeUnit.SECONDS)
@Fork(value = 1)
@State(Scope.Thread)
public class BinaryFlatMapPerf {
    @Param({ "1", "1000", "1000000" })
    public int times;

    Flowable<Integer> singleFlatMapPublisher;

    Flowable<Integer> singleFlatMapHidePublisher;
}

class Temp{
	public static <T> Function<SingleSource<? extends T>, Publisher<? extends T>> toFlowable() {
		//return Flowable.concat(Maybe.wrap(other).toFlowable(), toFlowable());
	}

	// return toFlowable().startWith(other);
}