package br.com.timachado.pitchstudio

import org.junit.Assert.*
import org.junit.Test

class StageRehearsalMathTest {
    @Test fun seekTenSecondsForwardAndBackward() {
        val n=44100L*100L
        assertEquals(.6,StageRehearsalMath.seek(.5,10.0,n,44100),1e-8)
        assertEquals(.4,StageRehearsalMath.seek(.5,-10.0,n,44100),1e-8)
        assertEquals(0.0,StageRehearsalMath.seek(.02,-10.0,n,44100),1e-8)
        assertEquals(1.0,StageRehearsalMath.seek(.98,10.0,n,44100),1e-8)
    }
    @Test fun rejectInvalidProjectsAndNonfiniteValues() {
        assertEquals(0.0,StageRehearsalMath.seek(.5,10.0,0L,44100),0.0)
        assertEquals(0.0,StageRehearsalMath.seek(Double.NaN,10.0,441000L,44100),0.0)
    }
    @Test fun rehearsalLoopNeedsOrderedMarkers() {
        assertFalse(StageRehearsalMath.validLoop(null,.5))
        assertFalse(StageRehearsalMath.validLoop(.6,.5))
        assertFalse(StageRehearsalMath.validLoop(.5,.501))
        assertTrue(StageRehearsalMath.validLoop(.2,.8))
    }
    @Test fun scrollSpeedsArePositiveAndMonotonic() {
        val a=StageRehearsalMath.scrollPixels(0,2f)
        val b=StageRehearsalMath.scrollPixels(1,2f)
        val c=StageRehearsalMath.scrollPixels(2,2f)
        assertTrue(a>0 && a<b && b<c)
    }
}
