"use client"

import AccountForm from "@/components/AccountForm";
import { Account } from "@/types/account";
import { useSearchParams } from "next/navigation";
import { useCallback } from "react";

interface Props {
    account: Account
}

export default function AccountFormContainer({ account } : Props) {
    const searchParams = useSearchParams();

    const onSubmit = useCallback(() => {
        window.location.href = searchParams.get("return") || "/";
    }, [searchParams]);

    return (
        <AccountForm account={account} onSubmitSuccess={onSubmit} />
    )
}
