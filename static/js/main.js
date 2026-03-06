/**
 * GIRO - Gestión Integral de Riesgo Operacional
 * JavaScript principal
 */

// ============================================================
// SIDEBAR TOGGLE (responsive)
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });

        // Cerrar sidebar al hacer clic fuera (mobile)
        document.addEventListener('click', function(e) {
            if (window.innerWidth <= 992) {
                if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('active');
                }
            }
        });
    }

    // Auto-cerrar alertas después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });
});

// ============================================================
// DATATABLES - Configuración en español
// ============================================================
const DATATABLES_ES = {
    processing: "Procesando...",
    search: "Buscar:",
    lengthMenu: "Mostrar _MENU_ registros",
    info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
    infoEmpty: "Mostrando 0 a 0 de 0 registros",
    infoFiltered: "(filtrado de _MAX_ registros totales)",
    loadingRecords: "Cargando...",
    zeroRecords: "No se encontraron registros",
    emptyTable: "No hay datos disponibles",
    paginate: {
        first: "Primero",
        previous: "Anterior",
        next: "Siguiente",
        last: "Último"
    },
    aria: {
        sortAscending: ": activar para ordenar ascendente",
        sortDescending: ": activar para ordenar descendente"
    }
};

// ============================================================
// FORMATEO DE MONTOS
// ============================================================
function formatMonto(valor) {
    if (!valor && valor !== 0) return '-';
    return new Intl.NumberFormat('es-DO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(valor);
}

// ============================================================
// CÁLCULO AUTOMÁTICO DE PÉRDIDA NETA
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    const brutaInput = document.querySelector('input[name="monto_perdida_bruta_dop"]');
    const recuperadoInput = document.querySelector('input[name="monto_recuperado_dop"]');
    const netaInput = document.querySelector('input[name="monto_perdida_neta_dop"]');

    if (brutaInput && recuperadoInput && netaInput) {
        function calcularNeta() {
            const bruta = parseFloat(brutaInput.value) || 0;
            const recuperado = parseFloat(recuperadoInput.value) || 0;
            netaInput.value = (bruta - recuperado).toFixed(2);
        }
        brutaInput.addEventListener('input', calcularNeta);
        recuperadoInput.addEventListener('input', calcularNeta);
    }
});
