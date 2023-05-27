## Uso obrigatório
<table>
    <tr>
        <th>Node</th>
        <th>Descrição</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1.Piece</th>
        <th>Tipo  de peça a remover do armazem para a máquina 1 (int); Escolher o tipo da peça antes de ativar o percurso</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.Piece</th>
        <th>Tipo  de peça a remover do armazem para a máquina 3 (int); Escolher o tipo da peça antes de ativar o percurso</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.Piece</th>
        <th>Tipo  de peça a remover do armazem para a máquina 4 (int); Escolher o tipo da peça antes de ativar o percurso</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1_1.WH_M1</th>
        <th>Ativa percurso do Warehouse para maquina 1; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.WH_M3</th>
        <th>Ativa percurso do Warehouse para maquina 3; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.WH_M4</th>
        <th>Ativa percurso do Warehouse para maquina 4; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M1.Dif_Time</th>
        <th>Tempo do percurso do Warehouse para maquina 1 (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M3.Dif_Time</th>
        <th>Tempo do percurso do Warehouse para maquina 3 (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.WH_M4.Dif_Time</th>
        <th>Tempo do percurso do Warehouse para maquina 4 (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M1_M2.M1_M2</th>
        <th>Ativa percurso da máquina 1 para maquina 2; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M1_M2.Dif_Time</th>
        <th>Tempo do percurso da máquina 1 para maquina 2 (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M1.cmd_stop</th>
        <th>Tempo que a máquina 1 vai permanecer em funcionamento (em segundos)(configurar antes de enviar peça pra máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M2.cmd_stop</th>
        <th>Tempo que a máquina 2 vai permanecer em funcionamento (em segundos)(configurar antes de enviar peça pra máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M3.cmd_stop</th>
        <th>Tempo que a máquina 3 vai permanecer em funcionamento (em segundos)(configurar antes de enviar peça pra máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.Geral.M4.cmd_stop</th>
        <th>Tempo que a máquina 4 vai permanecer em funcionamento (em segundos)(configurar antes de enviar peça pra máquina)(int)</th>
    </tr>
</table>

## Opcional
O codesys retirar as peças das máquinas automáticamente no fim do processsamento. Podes usar estas variaveis para teste
<table>
    <tr>
        <th>Node</th>
        <th>Descrição</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M2_WH.M2_WH</th>
        <th>Ativa percurso da maquina 2 para o Warehouse; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M2_WH.Dif_Time</th>
        <th>Tempo do percurso da maquina 2 para Warehouse (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M3_WH.M3_WH</th>
        <th>Ativa percurso da maquina 3 para o Warehouse; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M3_WH.Dif_Time</th>
        <th>Tempo do percurso da maquina 3 para Warehouse (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M4_WH.M4_WH</th>
        <th>Ativa percurso da maquina 4 para o Warehouse; Ligar variavel e ela desativa automáticamente (Booleano)</th>
    </tr>
    <tr>
        <th>ns=4;s=|var|CODESYS Control Win V3 x64.Application.M4_WH.Dif_Time</th>
        <th>Tempo do percurso da maquina 4 para Warehouse (sem considerar tempo de execução da máquina)(int)</th>
    </tr>
</table>
