"use client"

import { ReactNode, useEffect, useRef, useState } from "react";

interface Props {
    message: ReactNode;
    show: boolean;

    autoHideDurationMs?: number;

    variant: "error"; // Add more variants later
}

export default function SnackBar({ message, show, autoHideDurationMs }: Props) {
    const [render, setRender] = useState<boolean>(show);

    const timeoutRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        setRender(show);

        if (autoHideDurationMs && autoHideDurationMs > 0) {
            if (show) {
                timeoutRef.current = setTimeout(() => { setRender(false); }, autoHideDurationMs);
            } else if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }
        }
    }, [show, setRender, autoHideDurationMs]);

    if (!render) { return (<></>); }
    return (
        <div className="flex justify-center w-dvw fixed bottom-2.5">
            <div className="min-w-fit bg-red-600 text-white text-xs pt-3 pb-3 pr-4 pl-4  text-center">
                {message}
            </div>
        </div>
    );
}
