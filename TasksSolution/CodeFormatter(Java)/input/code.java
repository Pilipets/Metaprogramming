public class Foo {
    public int[] X = new int[]{1, 3, 5, 7, 9, 11};

    public void foo(boolean a, int x, int y, int z) {
        label1:
        do {
            switch (sdfdsfds) {
            };
            try {
                if (x > 0) {
                    int someVariable = a ? x : y;
                    int anotherVariable = a ? x : y;
                } else if (x < 0) {
                    int someVariable = (y + z);
                    someVariable = x = x + y;
                } else {
                    label2:
                    for (int i = 0; i < 5; i++) doSomething(i);
                }
                switch (a) {
                    case 0:
                        doCase0();
                        break;
                    default:
                        doDefault();
                }
            } catch (Exception e) {
                processException(e.getMessage(), x + y, z, a);
            } finally {
                processFinally();
            }
        }
        while (true);

        if (2 < 3) return;
        if (3 < 4) return;
        do {
            ++x;
        }
        while (x < 10000);
        while (x < 50000) x++;
        for (int i = 0; i < 5; i++) System.out.println(i);
    }

    private class InnerClass implements I1, I2 {
        public void bar() throws E1, E2 {
            List<?>           listUknown = new ArrayList<A>();
List<? extends A> listUknown = new ArrayList<A>();
List<? super   A> listUknown = new ArrayList<A>();
        }
    }

    public void processElements(List<? extends A> elements){
   for(A a : elements){
      System.out.println(a.getValue());
   }
}
}


@Annotation(param1 = "value1", param2 = "value2")
@SuppressWarnings({"ALL"})
public class Foo<T extends Bar & Abba, U> {
    int[] X = new int[]{1, 3, 5, 6, 7, 87, 1213, 2};
    int[] empty = new int[]{};

    public void foo(int x, int y) {
        Runnable r = () -> {
        };
        Runnable r1 = this::bar;
        for (int i = 0; i < x; i++) {
            y += (y ^ 0x123) << 2;
        }
        do {
            try (MyResource r1 = getResource(); MyResource r2 = null) {
                if (0 < x && x < 10) {
                    while (x != y) {
                        x = f(x * 3 + 5);
                    }
                } else {
                    synchronized (this) {
                        switch (e.getCode())
                        if (var > 3) while (x < 50000) {x++; var = 5; }
                        if (var > 3) for (x < 50000) x++; var = 5;
                        for(x - 3; 32; 233);
                    }
                }
            } catch (MyException e) {
            } finally {
                int[] arr = (int[]) g(y);
                x = y >= 0 ? arr[y] : -1;
                Map<String, String> sMap = new HashMap<String, String>();
                Bar.<String, Integer>mess(null);
            }
        }
        while (true);
    }

    void bar() {
        {
            return;
        }
    }
}

class Bar {
    static <U, T> U mess(T t) {
        return null;
    }

    public void setup() {
        Connection conn = getConnection();
        assert conn != null;
    }

    public void setup() {
        Connection conn = getConnection();
        assert conn != null : "Connection is null";
    }
}

interface Abba {
        Operationable op = new Operationable(){
         
                    public int calculate(int x, int y){
             
                        return x + y;
                    }
                };
}