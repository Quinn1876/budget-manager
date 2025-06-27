"use client"

import { Account } from "@/types/account"
import { Pie, PieChart, ResponsiveContainer } from "recharts"
import { PieLabelProps } from "recharts/types/polar/Pie";

interface Props {
    accounts: Account[]
    className?: string,
    width?: string,
    height?: string,
    textColor?: string
}

export default function AccountBalancePieChart({
    accounts,
    className,
    width,
    height,
    textColor
}: Props) {
    const renderCustomizedLabel = ({ cx, cy, midAngle, outerRadius, balance, index }: PieLabelProps) => {
        const RADIAN = Math.PI / 180;
        const radius = outerRadius + 35;
        const x = cx + radius * Math.cos(-(midAngle || 0) * RADIAN);
        const y = cy + radius * Math.sin(-(midAngle || 0) * RADIAN);

        return (
            <>
            <text x={x} y={y} fill={textColor || "white"} textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
                {`${(index != null && accounts[index].account_name) || "Unknown"}:`}
            </text>
            <text x={x} y={y+16} fill={textColor || "white"} textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
                {`$${(balance).toFixed(2)}`}
            </text>
            </>
        );
    };
    console.log(accounts)
    return (
        <ResponsiveContainer width={width || "60%"} height={height || "50%"} className={className}>
          <PieChart width={1900} height={350}>
            <Pie
              data={accounts}
              dataKey="balance"
              nameKey="account_name"
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              fill="#82ca9d"
              label={renderCustomizedLabel}
            />
          </PieChart>
        </ResponsiveContainer>
    );
}
